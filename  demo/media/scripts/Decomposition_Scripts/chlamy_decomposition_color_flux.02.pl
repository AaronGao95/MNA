#!/usr/bin/perl -w

#Make decomposition for YPD_medium (filtering extracellular reactions)
#print cycles and respective fluxes
use strict "vars";
###########################################################
my $condition = 'lna';
my $compartment = 'u';
###########################################################
my $path = "compartments\/$compartment\/$condition\/";
my $proj_name="$path" . "chlamydomonas_$condition.csv";
###########################################################
# Cofactors list

####################
my @Cofactors = (); #List of cofactors to be filtered is empty.

####################
#reading flux matrix
#and building adjacency matrix
my($Flux ,$Adj, $React, $Metab) = &read_flux_matrix("$proj_name",\@Cofactors);
my %FluxMatrix = %{$Flux};
my %FLUX = %FluxMatrix;
my %Adjacency = %{$Adj};
my @Reactions   = @{$React};
my @Metabolites = @{$Metab};
my @Nodes =(@Reactions, @Metabolites) ;

my @Cycles = ();


#my $k;
#foreach my $k1 ( keys %FluxMatrix){
#    foreach my $k2 (keys %{$FluxMatrix{$k1}}){
#	$k++;
#	print "$k\t$k1\t$k2\t$FluxMatrix{$k1}->{$k2}\n";
#    }
#}
#print join "*", @Reactions,"\n\n";
#print join "*", @Metabolites,"\n\n";
#exit;

####################
#   FLUX CONSERVATION ON INPUT
#my %Conservation = &conservation(\%FluxMatrix,\@Reactions);
#exit;


####################
# verify adjacency matrix consistency
my %Adj_test =%Adjacency;
#%Adjacency=  &verify_adjacency(\%Adj_test,@Cofactors);
#Eliminate node "Ground"
#exit;
####################



####################
# Cycle Enumeration and Translations
 @Cycles = &tanjan($proj_name,\%Adjacency,\@Nodes);

print"Cycles enumerated\n";

my @Cycles_to_print = @Cycles;

#for (my $c=0; $c <= $#Cycles;$c++){
#    print "@{$Cycles[$c]}\n";
#}
#&flux_matrix_print("$proj_name" ,\%FLUX,\@Reactions,\@Metabolites,\@Cycles_to_print);

# Currently used to print the graphs:
#&flux_color_print("$proj_name" ,\%FLUX,\@Reactions,\@Metabolites);
@Cycles_to_print=();


my $cycles_names = "$proj_name" . '_cycles_names.txt';  
open (CY, ">$cycles_names");
for (my $c=0; $c <= $#Cycles;$c++){
    print CY "@{$Cycles[$c]}\n";
}

####################


my %Acyclic = &decomposition(\@Cycles, \%FluxMatrix, $proj_name);


####################
#   FLUX CONSERVATION ON OUTPUT
# %Conservation = &conservation(\%Acyclic,\@Reactions);

foreach my $a (keys %Acyclic){

    foreach my $b (keys %{$Acyclic{$a}}){

	if (($Acyclic{$a}{$b} <= 0.001)){
	    #if (!(($a =~ /_out/) && ($b =~ /_out/) )){
		delete $Acyclic{$a}{$b};
	    #}
	}	
        #print"$a\t$b\t$Acyclic{$a}{$b}\n";
    }
}

my @NO_Cycles=();

#&flux_matrix_print("$proj_name" . "\.Acyclic",\%Acyclic,\@Reactions,\@Metabolites);
#&flux_color_print("$proj_name". "\.Acyclic" ,\%Acyclic,\@Reactions,\@Metabolites);

#for (my $c=0; $c <= $#Cycles;$c++){
#    print "@{$Cycles[$c]}\n";
#}
################
####################
#reading flux matrix
#and building adjacency matrix
#my($Flux2 ,$Adj2, $React2, $Metab2) = &read_flux_matrix("$proj_name",\@Cofactors);

#my %FluxMatrix2 = %{$Flux2};


################
#&acyclic_flux_matrix_print("$proj_name" . "\.Acyclic",\%FluxMatrix2,\@Reactions,\@Metabolites,\%Acyclic);
###########################################################################
###########################################################################
#                          SUBROTINES
###########################################################################
###########################################################################

sub decomposition{
    my @Cycles = @{$_[0]};
    my %Flux_Matrix = %{$_[1]};
    my $logfile = "$_[2]".".log";
    my $cycles_fluxes= 	"$_[2]"."_cycles_fluxes.txt";
    open(LOG , ">$logfile");
    open(CYFLU , ">$cycles_fluxes");
    my $step=0;
    while(1){
	last if( scalar (@Cycles) <=0 );
	print LOG "################################\n";
	print LOG "Decomposition  step $step\n";
	print LOG "################################\n";
	
	$step++;


#1-find critical arc with less flux in the network.
	my ($critical_arc,$critical_arc_flux,$cycles_prob)=&critical_arcs(\@Cycles,\%FluxMatrix);
	
	my %Critical_Arc=%{$critical_arc};
	my %Critical_Arc_Flux=%{$critical_arc_flux};
	my %Cycles_Prob=%{$cycles_prob};

	foreach my $h (keys %Critical_Arc){
	    #print "Critical arc\t Critical arc Flux Cycle Prob\n";
	    print LOG "CA @{$Critical_Arc{$h}->[0]}\t$Critical_Arc_Flux{$h}\n";
	}
    
	
#2-find nexus for corresponding critical arc in (1-)
	my (@cycles_in_nexus)= &get_nexus(\%Critical_Arc,\%Critical_Arc_Flux);
	my $critical_arc_ref= pop @cycles_in_nexus;
	my @nexus_critical_arc= @{$critical_arc_ref};
	
	#print ">>>>>>>>>>NEXUS: @cycles_in_nexus\t Critical Arc: @{$first_arc_ref}\n";
	my $nexus_size = scalar @cycles_in_nexus;


	#for (my $L =0 ; $L< scalar @Cycles; $L++){
	    #print LOG "Cycle $L =  @{$Cycles[$L]}\t Critical Arc: @{$Critical_Arc{$L}->[0]}\t Flux = $Critical_Arc_Flux{$L}\n";
	#    print LOG "Cycle $L =  @{$Cycles[$L]}\n";
	#}
	print LOG  ">> $nexus_size Cycles in Nexus: @cycles_in_nexus\n>>Critical arc = \($nexus_critical_arc[0] ,$nexus_critical_arc[1]\)\n";
	foreach my $n (@cycles_in_nexus){
	    print LOG "Cycle $n =  @{$Cycles[$n]}\n";
	    print CYFLU "@{$Cycles[$n]}\/$Critical_Arc_Flux{$n}\n";
	}
#sum over all cycle probabilities in nexus 
	
	#Starting Decomposition: 
	#1-) Find Flux distribution among cycles (according to cycles probabilities) in nexus. Critical Arc flux get null.
	
	my $total_prob;
	foreach my $c (@cycles_in_nexus){
	    $total_prob += $Cycles_Prob{$c}; 
	}
	foreach my $i (@cycles_in_nexus){
	    #
	    if ($total_prob==0){
		delete $Cycles[$i];
		print LOG  "CYCLE $i NOT SUBTRACTED\n";
		next;
	    }
            #

	    my $flux_to_subtract = ($Cycles_Prob{$i} * $Critical_Arc_Flux{$i})/$total_prob;
	    #=cut
	    #foreach my $i (@{$Cycles[$i]}){
	    #    print "Cycle $i: @{$Cycles[$i]})";
#
	    #}
	    #=cut
	    #print "Cycle $i @{$Cycles[$i]}\n";
	    #print "Cycle $i flux_to_subtract =  $flux_to_subtract\n";
	    my @nodes =  @{$Cycles[$i]};#nodes in corresponding Cycle.
	    
	    push @nodes, $Cycles[$i]->[0];
	    #print "Cycle $i @nodes\n";
	    #2-) Subtract corresponding amount of flux from %FluxMatrix
	    for(my $j=0; $j< scalar (@nodes) -1 ;$j++){
		#print " edges = $nodes[$j]  -- $nodes[$j+1]\n";
		$Flux_Matrix{$nodes[$j]}{$nodes[$j+1]} -= $flux_to_subtract;
	    }
	    #3-)delete Cycles in nexus from variable @Cycles	
	    
	    delete $Cycles[$i]; 
	    #$FluxMatrix{$nexus_critical_arc[0]}{$nexus_critical_arc[1]}=0;
	 
	}

	my @new_Cycles;
	for (my $k =0 ; $k< scalar @Cycles; $k++){
	    #print " Ciclos $k =  @{$Cycles[$k]} \n" if (exists($Cycles[$k]));
	    push @new_Cycles, [@{$Cycles[$k]}] if(exists($Cycles[$k] ));
	}
	
	@Cycles = @new_Cycles;


	#sleep(3);
	
    }


    close(LOG);
    return(%Flux_Matrix);
}  
#delete Nexus critical arc from %FluxMatrix 


sub read_flux_matrix{
    my $file = $_[0];
    my @Cofactors = @{$_[1]};
    my %FluxMatrix;
    my %Adj;
    my @Reactions;
    my @Metabolites;
    open(MASS,"<$file");
    my @data = <MASS>;
    foreach my $data (@data){
	chomp $data;
	$data =~ s/\"//g;
	next if(!( $data =~/->/));
	my @info = split /;/, $data;
	#info[0] "reaction" 
	#info[1]"Molar mass of compound";
	#info[2]"Molar flux 1";
	#info[3]"Mass flux 1";
	#info[4]"Balance"
	#info[5]"Molar flux 2";
	#info[6]"Mass flux 2";
	#info[7]"Balance";
	#$info[0] =~ s/\"//g;
	########################################varible defining massflux
	#print "$info[0]\t$info[1]\n";	
	my $flux = $info[1];
	if (abs($flux)<=0.00001){
	    next;
	}
	#next if ($flux==0);
	
	#if ($flux<0){
        #print "$info[0]\t$info[1]\n";
	#}
	#R_1AGPEAT1801819Z -> 1 G_single_R_1AGPEAT1801819Z	2.81232100402738;
	###################
	my @react = split /\s+->\s+/, $info[0];
	##R_1AGPEAT1801819Z	1 G_single_R_1AGPEAT1801819Z	u2.81232100402738;
	###################
	#stoichimetry elimination
        $react[0] =~ s/^\s*[\d\.]+\s+//;
	$react[1] =~ s/^\s*[\d\.]+\s+//;

	###################
	#extra spaces elimination
        $react[0] =~ s/\s+//g;
	$react[1] =~ s/\s+//g;

	#print ">>>>>>>>>>>>>>>> $info[0]\t>>>>>>>>>>>>>>>>>@react\n";
	###################
	# Cofactors Elimination
	if (grep /^$react[0]$/ , @Cofactors){
	    #print "Cofactor $react[0]\n";
	    next;
	} 
        if (grep /^$react[1]$/ , @Cofactors){
	  #print "Cofactor $react[1]\n";
	    next;
	}    
  
	###################

	foreach my $node (@react){
	    if (($node =~ /^R_\S+$/)){
		if( !( grep /^$node$/ ,  @Reactions)){
		    push @Reactions , $node ;
		}
	    }
	    else {
		if( !( grep /^$node$/ ,@Metabolites)){
		    push @Metabolites , $node;
		}
	    }
	}
        ###################


	if( $flux >= 0 ){
	    ${$FluxMatrix{$react[0]}}{$react[1]} = $flux;
	   
	}elsif ($flux< 0){
	    ${$FluxMatrix{$react[1]}}{$react[0]} = abs($flux);
	}
    }
    ##########
    # Building adjacency matrix
    my @Nodes = (@Reactions, @Metabolites);

   
    foreach my $key (@Nodes){
	if ( defined($FluxMatrix{$key})){
	    @{$Adj{$key}} = keys %{$FluxMatrix{$key}};
	}else{
	    @{$Adj{$key}} =();
	} 	
	##########
	
	
    }
    return(\%FluxMatrix, \%Adj, \@Reactions, \@Metabolites );
}


###############################################
#verify occurence of multiple edges
#
sub verify_adjacency{
    
    my %Adjacency=%{$_[0]};
    my %Ad_clean;
    foreach my $node (sort keys %Adjacency){

	#next if($node =~/Ground/ );

	#next if (!defined( scalar (@{$Adjacency{$node}}) ) );
	foreach my $reached_node ( @{$Adjacency{$node}} ){ 
	    if (!(grep /^$reached_node$/, @{$Ad_clean{$node}})){
		#next if($reached_node =~/Ground/ );
		push @{$Ad_clean{$node}},$reached_node;
		
		
		#print "$node\t$reached_node\t LIST = @{$Ad_clean{$node}}\n";
	    }else{
		print"ERROR:multiple edges in bipartite representation on:\n$node:\t$reached_node\t LIST @{$Ad_clean{$node}}\n"; 
	    }	
	}
    }
    return(%Ad_clean);
}

#########################
#Translating from reactions and metabolites to numbers as required by Tarjan algorithm

#Enumerate cycles

#Translate back to node names


sub tanjan{
    my $proj_name =$_[0];
    my %Adjacency = %{$_[1]};
    my @Nodes =    @{$_[2]};
    my $counter=0;
    my %Adjacency_Number;
    my %Adjacency_Name;
    
    #foreach my $k (keys %Adjacency){
#	print "*$k* \t","*",join "*", @{$Adjacency{$k}},"\n"; 
 #   }

    my $trans_file = "$proj_name" . "_reaction_translation.txt";
    open(TRANS, ">./$trans_file");
    foreach my $no (@Nodes){
	#print "$no:", join "\t", @{$Adjacency{$no}},"\n";
	$Adjacency_Number{$no}=$counter;
	$Adjacency_Name{$counter}=$no;
	print TRANS "$counter\t$no\n";
	
	$counter++;
	
    }
    close(TRANS);

    ###Printing Final Graph in the format required by Tarjans algorithm.
    #print"\>>>>>>>>>>>\n";

    my $graph_file = "grafo.txt";
    open(GRAPH,">./$graph_file");
    print GRAPH scalar @Nodes, "\n";
    foreach my $node (@Nodes){

	print GRAPH "$Adjacency_Number{$node} ";
	
	if(!defined($Adjacency{$node})){
	    print GRAPH "0 \n";
	    next;
	}else{
	    print GRAPH scalar @{$Adjacency{$node}}, " ";
	}
	foreach my $no (sort @{$Adjacency{$node}}){
	    if (defined ($Adjacency_Number{$no})){
		print GRAPH "$Adjacency_Number{$no} ";
	
	    }
	}
	print GRAPH "\n";
	
    }
    close(GRAPH);
    
    #####################################
    #Cycle enumeration
    #print"enumerating cycles...";
    system("bin64/tarjan.exe");
    #print"DONE\n";
    #####################################

    #####################################
    #Translate from tarjan
    open(CYC,"<ciclos.txt");
    my @cycles_file= <CYC>;
    my @Cycles;
    foreach my $cy (@cycles_file){
	chomp $cy;
	my @line = split /\s+/, $cy;
	my @new_line;
	foreach my $node (@line){
	    push @new_line ,$Adjacency_Name{$node};
	}
	push @Cycles, [@new_line];
    }
    #####################################


    #printing cycles
    open(CYCLES,">$proj_name.translated_cycles.txt");
    foreach (@Cycles){
	print CYCLES "@{$_}\n";
    }
    close(CYCLES);

    return(@Cycles);


}


sub get_nexus{
########################################
# Finding NEXUS to further decomposition
########################################
#1- find cicle C with smallest flux value for critical arcs
   my %Critical_Arc=%{$_[0]};
   my %Critical_Arc_Flux=%{$_[1]};




   my @crit_fluxes = sort numerically (values  %Critical_Arc_Flux);
   my $minimum_crit_flux= shift @crit_fluxes;
   print  LOG "Minimum Critical Flux = $minimum_crit_flux\n";
  my $cycle_min;
   foreach my $cyc (keys %Critical_Arc_Flux){
       if ($Critical_Arc_Flux{$cyc} <= $minimum_crit_flux){
	   $cycle_min=$cyc;
       }
   }       
=cut   
   foreach my $cycle(sort numerically (keys  %Critical_Arc_Flux)){
       #print"SUB GET NEXUS\n";
       #print" $cycle -> @{${$Critical_Arc{$cycle}}[0]} \t FLUX $Critical_Arc_Flux{$cycle}\n";
   }

   #comparing last and first element.
   my $last =  scalar (keys %Critical_Arc_Flux)-1; 
   my $cycle_min;#minimum value for critical arcs.
   if ($Critical_Arc_Flux{$last}<=$Critical_Arc_Flux{0}){
       $cycle_min= $last;
   }else{
       $cycle_min= 0;
   }
   
       for (my $i=0 ; $i < scalar (keys %Critical_Arc_Flux)-1; $i++){
	   my $fluxi=$Critical_Arc_Flux{$i};
	   my $fluxip=$Critical_Arc_Flux{$i+1};
	   if ($fluxi <=$fluxip){
	       $cycle_min = $i;
	   }
       }
=cut
   #print  LOG "Cycle with minimum value=\t$cycle_min\n";
   #print ">>>>>Critical_Arc_Flux $Critical_Arc_Flux{$cycle_min}\n";

   #
   ##############################################
   
   #for the cycle with smallest critical arc, get the critical arc (or simple one of them).
   #$first_arc_ref is a reference to critical arc of corresponding nexus.
   my $first_arc_ref = ${$Critical_Arc{$cycle_min}}[0];
   #print"teste    --------------------------------------------------------->>>>> @{$first_arc_ref}\n";
   my @cycles_in_nexus = &nexus_finder($cycle_min,$first_arc_ref , \%Critical_Arc);
   
   return(@cycles_in_nexus,$first_arc_ref);
}



sub nexus_finder{
    #called get_nexus 
    my $crit_cycle=$_[0]; #cycle with smallest critical arcs IN THE NETWORK. 
    my @critical_arc = @{$_[1]}; #critical arc in this cycle.
    my %Critical_Arc=%{$_[2]}; #critical arcs for all cycles.
    
    
    my $node0=$critical_arc[0];
    my $node1=$critical_arc[1];
    my @cycles_in_nexus;
    
    #print "looking for critical arc $node0 ,$node1\n";
    foreach my $cycle (sort numerically (keys  %Critical_Arc)){	
	#print "Cycle $cycle: @{$Cycles[$cycle]}\n";
	for (my $i=0 ; $i < scalar (@{$Critical_Arc{$cycle}}); $i++) {
	    #next if ($i==$crit_cycle);
	    if ($node0 eq ${${$Critical_Arc{$cycle}}[$i]}[0] && $node1 eq ${${$Critical_Arc{$cycle}}[$i]}[1]) {
		#print LOG ">>found cycle $cycle with critical arc \($node0, $node1\)\n";
		push @cycles_in_nexus,$cycle; 
	    }
	}
	#print"\n";
    }
    return(@cycles_in_nexus);
}
################

####
#Find Critical arcs

sub critical_arcs{
#returns 
#1-critical arcs for every cycle and  
#2-respective flux values for critical arcs
    my @Cycles =@{$_[0]};
    my %FluxMatrix=%{$_[1]};
    my @Critical_Arc=();
    my %Critical_Arc;
    my %Critical_Arc_Flux;
    my %Cycle_Prob;
    my @values;
    #my %flux_edges;
    my @critical_fluxes;
    my $min_critical_flux;
#############################################
#calculating edge of Maximum flux for complete network:
    foreach (keys %FluxMatrix){
	my @value = sort numerically (values %{$FluxMatrix{$_}});
	my $this_max= pop @value;
	push @values, $this_max;
    }
    
    @values = sort numerically (@values);
    my $flux_max = pop @values; 
    @values=undef;
#####################################
    
###############################
#Finding critical arc
    for (my $i=0; $i < scalar (@Cycles);$i++){
	#print "Cycle \#$i\n";
	my $critical_flux=$flux_max;
        my %flux_edges;
	$Cycle_Prob{$i}=1;
	#for each cycle, first node should be put also at the end of array in order 
	#to take into acount last edge 
	push @{$Cycles[$i]}, $Cycles[$i][0];
	
	#print join "\t", @{$Cycles[$i]},"\n";
	
	for(my $j=0; $j< scalar (@{$Cycles[$i]})- 1 ;$j++){
	    {		
		my($A,$B);
		($A,$B)=($Cycles[$i][$j],$Cycles[$i][$j+1]);
         	##############################
	        #Calculating Arc and Cycle  probability:
	        # Ratio = Total outcomming flux over $A/ Flux over edge ($A,$B)
	        ##############################		
		my $total_flux_outA;
		foreach my $flux_out (values %{$FluxMatrix{$A}}){
		     $total_flux_outA +=  $flux_out;
		}
		#print"Arc = ($A,$B) \t";
		my $prob_AB= ${$FluxMatrix{$A}}{$B}/$total_flux_outA;
		#print "$prob_AB \t ${$FluxMatrix{$A}}{$B}\n";
		$Cycle_Prob{$i} *= $prob_AB;
		###############################
		my $flux;
		#
		#print "$A\t$B\t${$FluxMatrix{$A}}{$B}\n";
		#
		if( defined (${$FluxMatrix{$A}}{$B})){
		    #print "$A\t$B\t${$FluxMatrix{$A}}{$B}\n";
		    $flux = ${$FluxMatrix{$A}}{$B};
		    
		}elsif (defined(${$FluxMatrix{$B}}{$A})){
		    #print "$B\t$A\t${$FluxMatrix{$B}}{$A}\n";
		    $flux = ${$FluxMatrix{$B}}{$A};
		    
		}else{
		    die "inconsitency in flux matrix:  arc $A $B has no corresponding flux value";
		}
		#print "\($A,$B\)->$flux\t" ;
		if ($flux <= $critical_flux){
		    $critical_flux= $flux;
		    push @{$flux_edges{$critical_flux}}, [$A,$B]; 
		}
	    }	    
	}
	#print "\n";	
	#print "Cycle $i Probability = $Cycle_Prob{$i}\n";
	my @fluxes=sort numerically (keys %flux_edges);
	my $flux_min = shift (@fluxes);
	@{$Critical_Arc{$i}}= @{$flux_edges{$flux_min}};
        $Critical_Arc_Flux{$i} = $flux_min;
	#push 	@{$Critical_Arc{$i}} , $flux_min; #every edge in this list has minimum value for the flux on the cycle
	#preparing output:
	pop @{$Cycles[$i]};
    }
    #returned hashes %Critical_Arc : key=Cycle index, value= reference to a listedges of triplets [nodeA, nodeB]
    #%Critical_Arc_flux  key=Cycle index, value= critical arc flux value
    
    my @out = (\%Critical_Arc,\%Critical_Arc_Flux,\%Cycle_Prob);
    
    return(@out);
}

sub numerically {$a <=> $b};


#######################################################################
#######################################################################
#######################################################################

#######################################################################
#DRAWING THE GRAPHS

sub flux_matrix_print {
    my $proj_name = $_[0];
    my %Acyclic=%{$_[1]};
    my @Reactions = @{$_[2]};
    my @Metabolites =  @{$_[3]};
    my @Cycles;
    if (!(defined($_[4]))){
       @Cycles=();
    }else{
	@Cycles=@{$_[4]};
    }
    my $dot_file ="$proj_name" . "_grafo.dot"; 
    my $ps_file ="$proj_name" . "_grafo.ps"; 
    my $gif_file="$proj_name" . "_grafo.gif";
    my $matrix_file ="$proj_name" . "_matrix.csv"; 
    my %Flux_Matrix;
    my %is_cycle;
    my %Cycles;

    my @largest_Cycles=();
    my %largest_Cycles;    
    ##################
    #preparing Cycles

    #1.find one of the largest cycles
    my $largest=0;
    for (my $c=0; $c <= $#Cycles; $c++){
	if (scalar(@{$Cycles[$c]}) >= scalar(@{$Cycles[$largest]}) ){
	    $largest =$c;
	}
    }

    if (scalar(@Cycles)>0){
	$largest = scalar(@{$Cycles[$largest]});
    }

    #2.find all cycles with maximum lenght

    for (my $c=0; $c <= $#Cycles; $c++){
	if (scalar(@{$Cycles[$c]}) == $largest ){
	    push @largest_Cycles, \@{$Cycles[$c]};
	    #print "@{$Cycles[$c]}\n";
	}
    }
    

    #3. BUILD A HASH STRUCTURE WITH ALL CYCLES.
    for (my $c=0; $c <= $#Cycles; $c++){
	for (my $k=0; $k< $#{$Cycles[$c]};$k++){
	    $Cycles{${$Cycles[$c]}[$k]}{${$Cycles[$c]}[$k+1]}=1;
	}
	my $last_elemt =$#{$Cycles[$c]};
	my $last_node=${$Cycles[$c]}[$last_elemt];
	my $first_node=${$Cycles[$c]}[0];
	$Cycles{$last_node}{$first_node}=1;
	#print "LAST LINK: $last_node -> $first_node\n";
    }

    #4.BUILD A HASH STRUCTURE WITH LARGEST CYCLES.

    for (my $c=0; $c <= $#largest_Cycles; $c++){
	#print "@{$largest_Cycles[$c]}\n";
	for (my $k=0; $k< $#{$largest_Cycles[$c]};$k++){
	    $largest_Cycles{${$largest_Cycles[$c]}[$k]}{${$largest_Cycles[$c]}[$k+1]}=1;
	}
	my $last_elemt =$#{$largest_Cycles[$c]};
	my $last_node=${$largest_Cycles[$c]}[$last_elemt];
	my $first_node=${$largest_Cycles[$c]}[0];
	$largest_Cycles{$last_node}{$first_node}=1;
	#print "LAST LINK: $last_node -> $first_node\n";
    }

    
    #################


    ##################
    # Writing .dot file
    
    open (DOT, ">$dot_file");
    print DOT "digraph G \{\n";
    print DOT "ratio=fill\;\n";
    print DOT "size=\"6,12\"\;\n"; 

    foreach my $re (@Reactions){
	print DOT "\"$re\" [style=\"setlinewidth(3)\",shape=box, fontsize=50]\;\n";
    }
    foreach my $me (@Metabolites){
	if ($me =~/_out/){
	    print DOT "\"$me\" [style=\"setlinewidth(3)\",fontsize=50,color =\".7 .3 1.0\",style=filled]\;\n";
	}else{
	    print DOT "\"$me\" [style=\"setlinewidth(3)\",fontsize=50]\;\n";
	}
    }

    foreach my $node (keys %Acyclic){
	foreach my $ad ( keys %{$Acyclic{$node}} ){
	    #verify if edge being drawn belogs to a cycle.
	    if (defined(${$largest_Cycles{$node}}{$ad} )) {
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(4)\", arrowsize=2,color=green]\;\n";
	    }elsif(defined(${$Cycles{$node}}{$ad} )) { 		
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(4)\", arrowsize=2,color=red]\;\n";
	    }else{
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(3)\", arrowsize=2] \;\n";
	    }

	}
    }
    print DOT "\}\n";
    close(DOT);
    ##################
   # my $COLOR_FLUX = 1;
    #if ($COLOR_FLUX){
	#my $dot_color_file ="$proj_name" . "_flux_color.dot";
	#my $ps_color_file ="$proj_name" . "_flux_color.ps";
	#my colo_code
    #}


    ##################
    # Generating figures.
    system("dot -Tps $dot_file -o $ps_file");
    system("dot -Tgif $dot_file -o $gif_file");



    ##################
    # Writing matrix (.csv) file
    open(MATRIX, "> $matrix_file");
    print MATRIX " ;";
    print MATRIX join ";",@Reactions,"\n";
    foreach my $me (@Metabolites) {
	print MATRIX "$me;";
	foreach my $re (@Reactions){
	    if (defined ($Acyclic{$re}{$me})){
		print MATRIX "$Acyclic{$re}{$me};";
	    }else{
		print MATRIX "0;"; 
	    }
	}
	print MATRIX "\n";
    }
    ################## 


   
}
#######################################################################


sub flux_color_print {
    my $proj_name = $_[0];
    my %Flux_Matrix= %{$_[1]};
    my @Reactions = @{$_[2]};
    my @Metabolites =  @{$_[3]};

    my $dot_file ="$proj_name" . "_flux_color.dot"; 
    my $ps_file ="$proj_name" . "_flux_color.ps"; 
    my $matrix_file ="$proj_name" . "_matrix.csv"; 
    my @colors=("darkviolet","royalblue","cyan","green","orange","red");

    my @range=(0,0.01,0.02,0.05,0.1,0.2,0.5);
    #if ($proj_name =~ /methylobacterium/){
    #@range=(0,.1,.2,.5,1,2,5);
    #}elsif($proj_name =~ /erythrocyte/){
    #	@range=(0,0.01,0.02,0.05,0.1,0.2,0.5);
    #}
    ##################
    # Writing .dot file
    open (DOT, ">$dot_file");
    print DOT "digraph G \{\n";
    print DOT "ratio=fill\;\n";
    #print DOT "size=\"7.5,11\"\;\n"; 
    print DOT "size=\"7.5,10\"\;\n"; 


    foreach my $re (@Reactions){
	print DOT "\"$re\" [shape=box,style=\"setlinewidth(3)\",fontsize=50]\;\n";
    }
    foreach my $me (@Metabolites){
	if ($me =~/_out/){
	    print DOT "\"$me\" [style=\"setlinewidth(3)\",fontsize=50,color =\".7 .3 1.0\",style=filled]\;\n";
	}elsif($me =~/_cofactors/){
	    print DOT "\"$me\" [shape=triangle,style=\"setlinewidth(3)\",fontsize=50,color=\"#FFD700\",style=filled,label=\"cof\"]\;\n";   
	}else{
	    print DOT "\"$me\" [style=\"setlinewidth(3)\",fontsize=50]\;\n";
	}
    }

    foreach my $node (keys %Flux_Matrix){
	#print DOT "\"$node\" -> \{";
	
	foreach my $ad ( keys %{$Flux_Matrix{$node}} ){
	    my $flux =${$Flux_Matrix{$node}}{$ad}/1000;
	    #print"$node\t$ad\t flux=$flux\n";
	    if (($flux > $range[0])&&($flux <= $range[1])) {
		#print"$colors[0]\n";
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(5)\",fontsize=50, arrowsize=3,color=$colors[0]]\;\n";
	    }elsif(($flux > $range[1])&&($flux <= $range[2])) {
		#print"$colors[1]\n";
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(5)\",fontsize=50,arrowsize=3,color=$colors[1]] \;\n";
	    }elsif(($flux > $range[2])&&($flux <= $range[3])) {
		#print"$colors[2]\n";
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(5)\",fontsize=50,arrowsize=3,color=$colors[2]] \;\n";
	    }elsif(($flux > $range[3])&&($flux <= $range[4])) {
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(5)\",fontsize=50,arrowsize=3,color=$colors[3]] \;\n";
		#print"$colors[3]\n";
	    }elsif(($flux > $range[4])&&($flux <= $range[5])) {
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(5)\",fontsize=50,arrowsize=3,color=$colors[4]] \;\n";
	    }elsif(($flux > $range[5])&&($flux <= $range[6])){
		#print"Black\n";
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(5)\",fontsize=50,arrowsize=3,color=$colors[5] ]\;\n";
	    }else{
		print DOT "\"$node\" -> \"$ad\" [style=\"setlinewidth(4)\",fontsize=50,arrowsize=3 ]\;\n";
	    }
	    
	}
    }
    print DOT "\}\n";
    close(DOT);
    ##################
    # Generating figures.
    system("dot -Tps $dot_file -o $ps_file");  
    ##################
    # Writing matrix (.csv) file
    open(MATRIX, "> $matrix_file");
    print MATRIX " ;";
    print MATRIX join ";",@Reactions,"\n";
    foreach my $me (@Metabolites) {
	print MATRIX "$me;";
	foreach my $re (@Reactions){
	    if (defined ($Acyclic{$re}{$me})){
		print MATRIX "$Acyclic{$re}{$me};";
	    }else{
		print MATRIX "0;"; 
	    }
	}
	print MATRIX "\n";
    }
    ##################
}
#######################################################################



#######################################################################
#######################################################################
#######################################################################
sub conservation {
    my %FluxMatrix=%{$_[0]};
    my @Nodes = @{$_[1]};
    my %FluxMatrix_T;
    my %Flux;

    foreach my $a (keys %FluxMatrix){
	foreach my $b (keys %{$FluxMatrix{$a}}){
	    $FluxMatrix_T{$b}->{$a} = - $FluxMatrix{$a}{$b};
	}
    }
    foreach my $node (@Nodes){
	my @total;
	if (defined ( keys %{$FluxMatrix{$node}} ) ){
	    foreach ( keys %{$FluxMatrix{$node}} ) {
		push @total , $FluxMatrix{$node}{$_};
		#print "$node\t$_\t$FluxMatrix{$node}{$_}\n";
	    }
	}
	if (defined ( keys %{$FluxMatrix_T{$node}} ) ){
	    foreach ( keys %{$FluxMatrix_T{$node}} ){
		push @total , $FluxMatrix_T{$node}{$_};
		#print "$node\t$_\t$FluxMatrix_T{$node}{$_}\n";
	    }
	}

	my $flux;
	foreach (@total){
	    $flux += $_;
	}
	$Flux{$node} = $flux;
	#print "SUM = @total\n";
	print"Node:$node\tFlux:$flux\n";
	
    }
    return(%Flux);
}


exit;
